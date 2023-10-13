import React from "react";
import PropTypes from "prop-types";

export default function Comment({
  handleCommentSubmit,
  handleTextChange,
  handleDeleteButton,
  commentText,
  comments,
  postid,
}) {
  /* Display and update comments */
  /*
    Yuning added a post prop to only show the input form when the post actually exist. 
    The reason is that cypress will click / type input as long as the component contains button/form.
    So when the fetch in post hasn't returned yet you need to make sure <Comment> component
    doesn't contain any button / input form because it's not properly initialized. Same is true for <Like>
    You could also use other prop as evidence. I'm not quite sure if use postid is ok in every situation.
     */
  return (
    <div>
      {comments &&
        comments.map((comment) => (
          <div key={comment.commentid}>
            <a href={comment.ownerShowUrl}>{comment.owner}: </a>
            <span data-testid="comment-text">{comment.text}</span>
            {comment.lognameOwnsThis && (
              <button
                type="button"
                data-testid="delete-comment-button"
                onClick={() => handleDeleteButton(comment.commentid)}
              >
                Delete comment
              </button>
            )}
          </div>
        ))}
      <div>
        {postid && (
          <form data-testid="comment-form" onSubmit={handleCommentSubmit}>
            <input
              type="text"
              value={commentText}
              onChange={handleTextChange}
            />
          </form>
        )}
      </div>
    </div>
  );
}

Comment.propTypes = {
  handleCommentSubmit: PropTypes.func.isRequired,
  handleTextChange: PropTypes.func.isRequired,
  handleDeleteButton: PropTypes.func.isRequired,
  commentText: PropTypes.string.isRequired,
  comments: PropTypes.instanceOf(Array).isRequired,
  postid: PropTypes.number.isRequired,
};
