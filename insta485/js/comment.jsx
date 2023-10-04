import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

export default function Comment({ handleCommentSubmit, handleTextChange, handleDeleteButton, commentText, comments }) {
    /* Display and update comments */
    return (
      <div>
        {comments?.map((comment) =>
          <div key = {comment.commentid}>
                <a href={comment.ownerShowUrl}>{comment.owner}: </a>
                <span data-testid="comment-text">{comment.text}</span>
                {comment.lognameOwnsThis ? (
                  <button data-testid="delete-comment-button" onClick={() => handleDeleteButton(comment.commentid)}>
                    Delete comment
                  </button>
                ) : (<></>)}
          </div>
        )}
        <div>
          <form data-testid="comment-form" onSubmit={handleCommentSubmit}>
            <input type="text" value={commentText} onChange={handleTextChange}/>
          </form>
        </div>
      </div>
    );
  }
  
  Comment.propTypes = {
    handleCommentSubmit: PropTypes.func,
    handleTextChange: PropTypes.func,
    handleDeleteButton: PropTypes.func,
    commentText: PropTypes.string,
    comments: PropTypes.array
  };
  