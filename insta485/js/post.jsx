import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import duration from "dayjs/plugin/duration";
import timezone from "dayjs/plugin/timezone";
import Comment from "./comment";
import Like from "./like";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */
  const [owner, setOwner] = useState("");
  const [imgUrl, setImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [created, setCreated] = useState("");
  const [postShowUrl, setPostShowUrl] = useState("");
  const [postid, setPostid] = useState(0);
  // for comment component
  const [comments, setComments] = useState([]);
  const [commentText, setCommentText] = useState("");
  const [commentsUrl, setCommentUrl] = useState("");
  // for like component
  const [numlike, setNumLike] = useState(0);
  const [likestatus, setLikeStatus] = useState(false);
  const [likeurl, setLikeUrl] = useState("");

  useEffect(() => {
    // Declare a boolean flag that we can use to cancel the API request.
    let ignoreStaleRequest = false;

    // Call REST API to get the post's information
    fetch(url, { credentials: "same-origin" })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        // If ignoreStaleRequest was set to true, we want to ignore the results of the
        // the request. Otherwise, update the state to trigger a new render.
        if (!ignoreStaleRequest) {
          // humanize the created time
          dayjs.extend(relativeTime);
          dayjs.extend(utc);
          dayjs.extend(duration);
          dayjs.extend(timezone);
          const curTime = dayjs.utc();
          const localCurTime = curTime.local();
          const localCreatedTime = dayjs(data.created)
            .utc("z")
            .local()
            .tz("America/Detroit");
          const timeDiff = localCreatedTime.diff(localCurTime);
          const humanizedTime = dayjs.duration(timeDiff).humanize(true);

          setComments([...data.comments]);
          setOwner(data.owner);
          setOwnerShowUrl(data.ownerShowUrl);
          setImgUrl(data.imgUrl);
          setCreated(humanizedTime);
          setPostShowUrl(data.postShowUrl);
          setOwnerImgUrl(data.ownerImgUrl);
          setCommentUrl(data.comments_url);
          setPostid(data.postid);
          setLikeStatus(data.likes.lognameLikesThis);
          setLikeUrl(data.likes.url);
          setNumLike(data.likes.numLikes);
        }
      })
      .catch((error) => console.log(error));

    return () => {
      // This is a cleanup function that runs whenever the Post component
      // unmounts or re-renders. If a Post is about to unmount or re-render, we
      // should avoid updating state.
      ignoreStaleRequest = true;
    };
  }, [url]);

  // get the handleTextChange event value and set the text to the value
  const handleTextChange = (e) => {
    setCommentText(e.target.value);
  };

  // send a POST request to create a new comment and update the comments state
  const handleCommentSubmit = async (e) => {
    // prevent the page from reloading
    e.preventDefault();
    // empty comment
    if (commentText.trim() === "") {
      return;
    }
    fetch(`${commentsUrl}`, {
      credentials: "same-origin",
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: commentText }),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        setComments([...comments, data]);
        setCommentText("");
      })
      .catch((error) => console.log(error));
  };

  // send the DELETE request to the API based on the id passed from the button
  const handleDeleteButton = async (commentid) => {
    fetch(`/api/v1/comments/${commentid}/`, {
      credentials: "same-origin",
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        // remove the comment from the comments state
        setComments(
          comments.filter((comment) => comment.commentid !== commentid),
        );
      })
      .catch((error) => console.log(error));
  };
  // Handle like & unlike in one handler
  const handleClick = async (
    cnumlike,
    clikestatus,
    clikeurl,
    cpostid,
    csetLikeUrl,
    csetLikeStatus,
    csetNumLike,
  ) => {
    fetch(
      clikestatus
        ? clikeurl
        : `/api/v1/likes/?${new URLSearchParams({
            postid: cpostid,
          })}`,
      {
        credentials: "same-origin",
        method: clikestatus ? "DELETE" : "POST",
      },
    )
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        if (response.status === 201) return response.json();
        return null;
      })
      .then((data) => {
        if (data) {
          csetLikeUrl(data.url);
          csetLikeStatus(true);
          csetNumLike(cnumlike + 1);
        } else {
          csetLikeStatus(false);
          csetNumLike(cnumlike - 1);
        }
      })
      .catch((error) => console.log(error));
  };

  const handleDoubleClick = async () => {
    if (!likestatus) {
      fetch(
        `/api/v1/likes/?${new URLSearchParams({
          postid,
        })}`,
        {
          credentials: "same-origin",
          method: "POST",
        },
      )
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          if (response.status === 201) return response.json();
          return null;
        })
        .then((data) => {
          if (data) {
            setNumLike(numlike + 1);
            setLikeStatus(!likestatus);
            setLikeUrl(data.url);
          }
        })
        .catch((error) => console.log(error));
    }
  };
  if (postid)
    return (
      <div className="posts">
        <div>
          <a href={ownerShowUrl}>
            <img src={ownerImgUrl} alt="owner_profile" className="profiles" />
            {owner}
          </a>
          <a href={postShowUrl} className="created">
            {created}
          </a>
        </div>
        <img
          src={imgUrl}
          alt="post_image"
          className="post_img"
          onDoubleClick={handleDoubleClick}
        />
        <div>
          <Like
            handleClick={handleClick}
            numlike={numlike}
            likestatus={likestatus}
            likeurl={likeurl}
            postid={postid}
            setLikeStatus={setLikeStatus}
            setLikeUrl={setLikeUrl}
            setNumLike={setNumLike}
          />
        </div>
        <div>
          <Comment
            key={postid}
            handleTextChange={handleTextChange}
            handleCommentSubmit={handleCommentSubmit}
            handleDeleteButton={handleDeleteButton}
            commentText={commentText}
            comments={comments}
            postid={postid}
          />
        </div>
      </div>
    );
  return <h4>Loading...</h4>;
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};
